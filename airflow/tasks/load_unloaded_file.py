def load_unloaded_file(db):
    results = db.execute("SELECT id WHERE documents WHERE processed=false")
    return [{"id": result[0]} for result in results]