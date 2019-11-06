# STARS Docker Environment

Dockers help us work around extremely outdated dependencies.

## Up and running

You'll need `docker` and `docker-compose` installed.

Create an .env.dev file to store you local environment variables. Use `.env.dev-template` as a reference.

Start your dockers

```
docker-compose up
```

Run an initial data import:

```
mysql stars -h 127.0.0.1 -P 3306 -u root -p < /path/to/import.sql
```
