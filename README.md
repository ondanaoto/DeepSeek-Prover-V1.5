# How to use
## 1. Attach the DeepSeek container.
```bash
docker exec -it your_dsp_container_name /bin/bash
```
## 2. Run the following command.
```bash
python -m prover.launch --config=configs/test.py
```
Then you can see the log of generated proofs in the `/data/logs` directory.
