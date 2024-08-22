#/bin/sh
cd /opt/frontend
nohup /bin/bash -c npm run start &
cd /opt/
daphne -b 0.0.0.0 -p 8000 plo_project.asgi:application
#nohup /bin/sh -c python3 /opt/poker/cli_game &
