# STARS Docker Environment

Dockers help us work around extremely outdated dependencies.

## Up and running

### Requirements

You'll need `docker` and `docker-compose` installed.

Create an .env.dev file to store you local environment variables. Use `.env.dev-template` as a reference.

Add any .sql file you'd like to `docker/docker-entrypoint-initdb.d` to initially populate the `stars` database.

### Start your dockers

```
cd docker
docker-compose up
```

Note: Sometimes `msyql` may come up before `web` during initial build, which breaks django. Simply close containers and `docker-compose up` again to get it working again. It would probably be worthwhile getting `wait-for-it.sh` to work...

### Run setup scripts as necessary

```
cd docker
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```

There's probably a better way to share the source and static between worker and web, but we can work on that later if necessary...

Visit: http://localhost:8000/tool/

### Connecting to the shell

```
docker-compose exec web python manage.py shell
```

Swap `web` for `worker` if you're trying to connect to that container.

## Notes

### Static and temporary files

Temporary files need to be shared across the web and worker containers to mimic the current deployment. `/tmp` is therefore a shared volume between those containers.

Static files are also on a shared volume `static` at `/usr/static`.
