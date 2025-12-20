# freeagent

`freeagent` is a python library for using the freeagent API.

## Initial setup

Create an API app entry at the [Freeagent Dev Portal](https://dev.freeagent.com)

When run if they id and secret entries do not exist they will be prompted for.

Manual setup example on macOS

1. Set the client ID
security add-generic-password -a freeagent_client_id -s freeagent_api \
    -w "your_client_id_here" -U

2. Set the client secret
security add-generic-password -a freeagent_client_secret -s freeagent_api \
    -w "your_client_secret_here" -U

If you want to clear the oauth token from Keychain, you can run this once:
security delete-generic-password -a "oauth2_token" -s "freeagent_token"

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
