import psutil
from db.database import init_db
from ui.dashboard import App
process = psutil.Process()


init_db()

app = App()
app.mainloop()
print(process.memory_info().rss / 1024 ** 2)