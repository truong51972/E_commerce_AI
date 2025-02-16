FROM cloudflare/cloudflared:latest

CMD ["tunnel", "run"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 CMD cloudflared --version