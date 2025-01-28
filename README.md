# E_commerce_AI

## Technology:

#### Back End
- Django
- Django Rest Framework

#### Database:
- PostgreSQL
- Milvus 

#### AI:
- Ollama
- Langchain

#### Deployment:
- Cloudflare
- Docker




### Bonus
#### Script increase buffer size
create in _username_.wslconfig
copy below
```
######COPY######
[wsl2]
kernelCommandLine = "sysctl.net.core.rmem_max=8388608 sysctl.net.core.wmem_max=8388608"
```