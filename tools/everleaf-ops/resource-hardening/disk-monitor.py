#!/usr/bin/python3
import shutil,sys
u=shutil.disk_usage("/"); pct=100*u.used/u.total; free=u.free/1024**3
level="CRITICAL" if pct>=90 or free<10 else "WARNING" if pct>=80 or free<20 else "OK"
print(f"{level} root_used={pct:.1f}% free={free:.1f}GiB",flush=True)
sys.exit(1 if level=="CRITICAL" else 0)
