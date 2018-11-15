# Crowdsale

## Overview

* Provide a sample implementation of crowdsale.

## Deployment

```bash
$ tbears deploy -k <keystore_file> -c crowdsale.json sample_crowdsale
```
Note that `_tokenScore` parameter needs to be updated properly with your actual deployed token SCORE address.

## Test
The sample_crowdsale test requires the irc2_token SCORE source code
```bash
$ tbears test sample_crowdsale
```
## References

* [ICON Token Standard](https://github.com/icon-project/IIPs/blob/master/IIPS/iip-2.md)

