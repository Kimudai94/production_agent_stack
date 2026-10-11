import subprocess
import time
from rich.live import Live
from rich.table import Table

def get_nvidia_gpu_memory():
    """Holt aktuelle VRAM-Nutzung"""
    try:
        output = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=memory.total,memory.used,memory.free', '--format=csv']
        ).decode()
        
        lines = output.strip().split('\n')[1:]  # Header skippen
        memory_total = int(lines[0].split(',')[0].strip().replace(' MiB', ''))
        memory_used = int(lines[0].split(',')[1].strip().replace(' MiB', ''))
        
        return memory_total, memory_used
    except:
        return None, None

def monitor_vram(interval=2):
    """Live VRAM Monitor für CLI"""
    
    with Live(console=None, refresh_per_second=1/interval) as live:
        while True:
            total, used = get_nvidia_gpu_memory()
            
            if total and used:
                table = Table(title="NVIDIA GPU Memory")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", justify="right")
                
                table.add_row("Total", f"{total} MiB")
                table.add_row("Used", f"{used} MiB")
                table.add_row("Free", f"{total - used} MiB")
                table.add_row("Utilization", f"{(used/total)*100:.1f}%")
                
                live.update(table)
            
            time.sleep(interval)

if __name__ == "__main__":
    monitor_vram()