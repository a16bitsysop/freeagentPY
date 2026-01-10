# freeagent

`freeagent` is a python library for using the freeagent API.

## Initial setup

Create an API app entry at the [Freeagent Dev Portal](https://dev.freeagent.com)

## Exmple

```python
from os import environ
import json

from freeagent import FreeAgent

def _load_token():
    with open("token.json", "r") as f:
        token = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        token = None
    return token

def _save_token(token_data):
    # save the token
    with open("token.json", "w") as f:
        json.dump(token_data, f)

client_id = environ["FREEAGENT_ID"]
client_secret = environ["FREEAGENT_SECRET"]

token = _load_token()

freeagent_client = FreeAgent()
freeagent_client.authenticate(client_id, client_secret ,_save_token, token)

main_response = freeagent_client.get_api("users/me")
print(
f"✅ Authenticated! User info: {main_response['user']['first_name']} {main_response['user']['last_name']}"
)

paypal_id = freeagent_client.bank.get_first_paypal_id()
paypal_data = freeagent_client.bank.get_unexplained_transactions(paypal_id)
```

## Documentation

Full documentation is available at  
👉 [https://a16bitsysop.github.io/freeagentPY/](https://a16bitsysop.github.io/freeagentPY/)

---

## Running Tests

Run tests:

```bash
pytest
```

## Contributing

Contributions are welcome! Please:

1. Fork the repo
2. Create your feature branch `git checkout -b my-feature`
3. Edit the source code to add and test your changes
4. Commit your changes `git commit -m 'Add some feature'`
5. Push to your branch `git push origin my-feature`
6. Open a Pull Request

Please follow the existing code style and write tests for new features.

---

## License

This project is licensed under the MIT [MIT License](https://github.com/a16bitsysop/freeagentPY/blob/main/LICENSE).

---

## Contact

Created and maintained by Duncan Bellamy.
Feel free to open issues or reach out on GitHub.

---
