#!/bin/bash
export FLASK_APP=app.main
flask db init || true
flask db migrate -m "Automated migration" || true
flask db upgrade
exec "$@"
