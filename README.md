# Sample SCOREs

A sample has following structure. 

```
sample
├──my_score
   ├── __init__.py
   ├── my_score.py
   ├── package.json
   ├── ...
├──tests
├──README.md
├──deploy.json
```

**SCORE deployment** 

```bash
$ tbears deploy -k <keystore_file> [-c deploy.json] my_score
```

"deploy.scoreParams" in "deploy.json" defines the input parameter values of `on_install()` method. If `on_install()` does not take any input parameters, `-c deploy.json` option is not necessary.  

```json
    ...
    "deploy": {
        "contentType": "zip",
        "mode": "install",
        "scoreParams": {
            "input_param_1": "0x3e8",
            "input_param_2": "0x12"
        }
    }
```

Reference

- [T-Bears deploy command](https://github.com/icon-project/t-bears/blob/master/README.md#tbears-deploy)