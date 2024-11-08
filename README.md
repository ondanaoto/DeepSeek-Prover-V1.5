
# SETUP

```
$ git clone https://github.com/yuta0x89/DeepSeek-Prover-V1.5
$ cd DeepSeek-Prover-V1.5
$ git submodule update --init
```

# docker build

```
$ cd DeepSeek-Prover-V1.5
$ docker build . -t deepseek-prover --no-cache 
```

# docker run

```
$ cd DeepSeek-Prover-V1.5
$ docker run -v .:/app --name DSPCONTAINER --gpus all -it deepseek-prover /bin/bash
```

```
$ docker start DSPCONTAINER
$ docker exec -it DSPCONTAINER /bin/bash
```

# Note
- Mathlib4 is moved and built at `/var/mathlib4` in DSPCONTAINER.
