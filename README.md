# freeagent

`freeagent` is a python library for using the freeagent API.

## Initial setup

Create an API app entry at the [Freeagent Dev Portal](https://dev.freeagent.com)

## Example

```python
from os import environ
from pathlib import Path
import json

from freeagent import FreeAgent

TOKEN_PATH = Path.home() / ".config" / "freeagent" / "token.json"

def _load_token():
    try:
        return json.loads(TOKEN_PATH.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def _save_token(token_data):
    # save the token
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(json.dumps(token_data, indent=2))

client_id = environ["FREEAGENT_ID"]
client_secret = environ["FREEAGENT_SECRET"]

token = _load_token()

freeagent_client = FreeAgent()
freeagent_client.authenticate(client_id, client_secret, _save_token, token)

paypal_id = freeagent_client.bank_account.get_first_paypal_id()
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
