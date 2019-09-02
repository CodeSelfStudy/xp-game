from fabric import task


@task
def deploy(c):
    """
    Deploys the project to the specified host. Expects the server to be
    configured as follows:
        - project repository located at ~/xp-game/
        - a systemd service configured with the name xpgame
        - static files to be served from /var/www/xpgame.com/
        - a virtualenv called venv located in the project directory
    """
    with c.cd('~/xp-game'):
        c.run("git pull", echo=True)
        c.run("source venv/bin/activate && pip install -r requirements.txt",
              echo=True)
        c.run("tsc", echo=True)
        c.run("sudo cp -r server/static/ /var/www/xpgame.com/", pty=True, echo=True)
        c.run("sudo systemctl restart xpgame", pty=True, echo=True)
        print("Deploy completed")
