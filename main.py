from db.database import init_db
from ui.dashboard import App

init_db()

app = App()
app.mainloop()   