# Zena fork of aegra

Fork of [ibbybuilds/aegra](https://github.com/ibbybuilds/aegra). Upstream files are **not modified**. Zena-specific integration lives in files named `*.zena.*`.

## Added files

| File | Purpose |
|------|---------|
| `aegra.zena.json` | Graph registry for 9 zena agents. Mounted at `/app/aegra.zena.json`; selected via `AEGRA_CONFIG` env var. |
| `docker-compose.zena.dev.yml` | Dev compose overlay. Brings up `aegra-postgres`, `aegra-api` (with `../langgraph` mounted as graph code), `aegra-cors-proxy` (nginx), `aegra-cloudflared` (tunnel to Studio). No Redis — uses in-process executor (`REDIS_BROKER_ENABLED=false`) per upstream dev-mode guidance. |
| `nginx-zena-dev.conf` | CORS proxy config; allowlists `smith.langchain.com` and `localhost:3001` (Agent Chat UI). |

## How to pull upstream

```bash
git remote add upstream https://github.com/ibbybuilds/aegra.git   # once
git fetch upstream
git merge upstream/main
```

Zena-specific files use distinct names (`*.zena.*`) and do not conflict with upstream, so merges should be clean.

## How this runs

Launched from the root zena repo:
```bash
cd /home/user/zena
make up
```
Root `docker-compose.dev.yml` includes `aegra/docker-compose.zena.dev.yml`.

External access:
- `http://localhost:${AEGRA_API_PORT}` — via local nginx CORS proxy.
- `https://${AEGRA_PUBLIC_URL}` — via Cloudflare tunnel (used by LangGraph Studio at smith.langchain.com).

Internal (inside docker network): `http://aegra-api:2026`.

Apifast switches to aegra by setting `LANGGRAPH_URL_DOCKER=http://aegra-api:2026` in `../deploy/dev.env` and restarting.

## Key env vars (see ../deploy/dev.env.example)

| Var | Purpose |
|-----|---------|
| `AEGRA_API_PORT` | Host-published port (nginx → aegra) |
| `AEGRA_DATABASE_URL` | Passed into container as `DATABASE_URL` |
| `AEGRA_AUTH_TYPE` | Passed as `AUTH_TYPE` (noop or custom) |
| `AEGRA_POSTGRES_DB/USER/PASSWORD` | aegra-postgres bootstrap |
| `AEGRA_CLOUDFLARE_TUNNEL_TOKEN` | Cloudflare tunnel authentication |
| `AEGRA_PUBLIC_URL` | For reference — the tunnel's public hostname |
