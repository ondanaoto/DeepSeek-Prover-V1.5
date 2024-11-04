
# SETUP

```
$ git clone https://github.com/yuta0x89/DeepSeek-Prover-V1.5
$ cd DeepSeek-Prover-V1.5
$ git submodule update --init
```

# docker run

```
$ cd DeepSeek-Prover-V1.5
$ docker pull ghcr.io/yuta0x89/deepseek-prover
$ docker run -v .:/app --name DSPCONTAINER --gpus all -it ghcr.io/yuta0x89/deepseek-prover /bin/bash
```

```
$ docker start DSPCONTAINER
$ docker exec -it DSPCONTAINER /bin/bash
```

# docker build

```
$ cd DeepSeek-Prover-V1.5
$ git submodule update --init # Run this if mathlib4 has not been cloned yet
$ docker build . -t deepseek-prover --no-cache 
```

# Note
- Mathlib4 is moved and built at `/var/mathlib4` in DSPCONTAINER.
- Ask yuta0x89 for Personal access tokens of dghcr.io/yuta0x89/deepseek-prover image.
