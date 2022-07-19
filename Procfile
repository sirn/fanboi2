web: ${VENV:-./venv}/bin/fbctl serve --reload
worker: ${VENV:-./venv}/bin/fbcelery worker
beat: ${VENV:-./venv}/bin/fbcelery beat
assets: pnpm exec gulp build watch
