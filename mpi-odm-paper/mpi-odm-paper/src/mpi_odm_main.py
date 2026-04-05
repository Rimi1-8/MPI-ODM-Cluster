import os
import sys
import time
from pathlib import Path

# Ensure src/ is on the path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from mpi4py import MPI
from pyodm import Node
from utils import load_config, get_node_by_rank, list_images, ensure_dir, write_json


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


def run_odm_task(cfg):
    """Submit image chunk to NodeODM and wait for processing."""
    node_info = get_node_by_rank(cfg, rank)
    host = node_info["host"]
    port = cfg["nodeodm_port"]

    chunk_dir = os.path.join(cfg["chunks_dir"], f"chunk_{rank}")
    result_dir = os.path.join(cfg["results_dir"], f"node_{rank}")
    ensure_dir(result_dir)

    images = list_images(chunk_dir)
    if not images:
        print(f"[Rank {rank}] WARNING: No images in {chunk_dir}")
        return {
            "rank": rank,
            "host": host,
            "status": "no_images",
            "elapsed_minutes": 0.0,
            "result_dir": result_dir,
            "num_images": 0
        }

    odm_options = cfg.get("odm_options", {})

    print(f"[Rank {rank}] Connecting to NodeODM at {host}:{port}")
    print(f"[Rank {rank}] Images: {len(images)}")
    print(f"[Rank {rank}] ODM options: {odm_options}")

    try:
        node = Node(host, port)
        # Verify connection
        info = node.info()
        print(f"[Rank {rank}] NodeODM version: {info.version}, engine: {info.engine}")
    except Exception as e:
        print(f"[Rank {rank}] ERROR connecting to NodeODM at {host}:{port}: {e}")
        return {
            "rank": rank,
            "host": host,
            "status": "connection_error",
            "error": str(e),
            "elapsed_minutes": 0.0,
            "result_dir": result_dir,
            "num_images": len(images)
        }

    start = time.time()
    try:
        task = node.create_task(images, options=odm_options)
        print(f"[Rank {rank}] Task created: {task.uuid}")
    except Exception as e:
        print(f"[Rank {rank}] ERROR creating task: {e}")
        return {
            "rank": rank,
            "host": host,
            "status": "task_creation_error",
            "error": str(e),
            "elapsed_minutes": round((time.time() - start) / 60.0, 2),
            "result_dir": result_dir,
            "num_images": len(images)
        }

    # Poll until done
    last_msg = ""
    while True:
        try:
            info = task.info()
            status_val = getattr(info.status, 'value', str(info.status))
            progress = info.progress
            msg = f"[Rank {rank}] status={status_val} progress={progress}%"
            if msg != last_msg:
                print(msg, flush=True)
                last_msg = msg

            if status_val in (30, 40, 50) or str(status_val) in ("30", "40", "50", "TaskStatus.COMPLETED", "TaskStatus.FAILED", "TaskStatus.CANCELED", "COMPLETED", "FAILED", "CANCELED"):
                break
        except Exception as e:
            print(f"[Rank {rank}] Warning polling task: {e}", flush=True)

        time.sleep(10)

    info = task.info()
    elapsed = round((time.time() - start) / 60.0, 2)
    final_status = getattr(info.status, 'value', str(info.status))

    if final_status not in (40, "40", "TaskStatus.COMPLETED", "COMPLETED"):
        print(f"[Rank {rank}] Task FAILED with status={final_status}")
        return {
            "rank": rank,
            "host": host,
            "status": "failed",
            "status_code": final_status,
            "elapsed_minutes": elapsed,
            "result_dir": result_dir,
            "num_images": len(images)
        }

    print(f"[Rank {rank}] Task COMPLETED in {elapsed} minutes. Downloading assets...")
    try:
        task.download_assets(result_dir)
        print(f"[Rank {rank}] Assets downloaded to {result_dir}")
    except Exception as e:
        print(f"[Rank {rank}] Ignorable error downloading assets (Windows zip): {e}")

    return {
        "rank": rank,
        "host": host,
        "status": "completed",
        "elapsed_minutes": elapsed,
        "result_dir": result_dir,
        "num_images": len(images)
    }


def main():
    cfg = load_config()

    if size != len(cfg["nodes"]):
        if rank == 0:
            print(f"ERROR: MPI size={size}, but config has {len(cfg['nodes'])} nodes.")
        return

    if rank == 0:
        print(f"=== MPI-ODM Distributed Processing ===")
        print(f"  Nodes: {size}")
        print(f"  NodeODM port: {cfg['nodeodm_port']}")
        print(f"  Chunks dir: {cfg['chunks_dir']}")
        print(f"  Results dir: {cfg['results_dir']}")
        print()

    comm.Barrier()
    local_result = run_odm_task(cfg)
    comm.Barrier()

    gathered = comm.gather(local_result, root=0)

    if rank == 0:
        summary_path = os.path.join(cfg["final_dir"], "mpi_summary.json")
        write_json(summary_path, gathered)

        print("\n=== MPI RUN SUMMARY ===")
        total_time = 0.0
        for item in gathered:
            status_icon = "OK" if item["status"] == "completed" else "FAIL"
            print(f"  [{status_icon}] Rank {item['rank']} ({item['host']}): "
                  f"{item['status']} | {item['num_images']} images | {item['elapsed_minutes']} min")
            if item["status"] == "completed":
                total_time = max(total_time, item["elapsed_minutes"])

        print(f"\nTotal parallel time: {total_time} minutes")
        print(f"Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()