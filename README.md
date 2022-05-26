# Scraping service
A service which scrapes the data from the given resources and distributes it among configured integrations.

### Tools:
- `poetry`: 
  - https://davebaker.me/2020/07/19/setting-up-django-project-with-poetry/
  - https://python-poetry.org/docs/
  
### Integrations:
- Because of the lack of any kind of proxy server, for now to configure hook urls for integrations provide a public IP address
of the host:
```bash
ip route get 1 | awk '{print $7}'
```
  