# Mathematical Proof API

This API provides endpoints for generating and reading mathematical proofs using the DeepSeek-Prover model and Lean 4 verifier.

## Running the API

```bash
cd /app
python -m api.main
```

The API will be available at http://localhost:8000

## API Documentation

Once the API is running, you can access the Swagger UI documentation at http://localhost:8000/docs or the ReDoc documentation at http://localhost:8000/redoc.

## Endpoints

### POST /api/prove

Start a proof generation task.

**Request Body:**

```json
{
  "data_path": "datasets/minif2f.jsonl",
  "data_split": null,
  "data_repeat": 1,
  "lean_max_concurrent_requests": 64,
  "lean_memory_limit": 10,
  "lean_timeout": 300,
  "batch_size": 32,
  "model_path": "deepseek-ai/DeepSeek-Prover-V1.5-RL",
  "mode": "cot", // Only 'cot' or 'non-cot' are allowed
  "temperature": 1.0,
  "max_tokens": 2048,
  "top_p": 0.95,
  "n_search_procs": 64,
  "algorithm_kind": "Sampling", // Only 'Sampling' or 'RMaxTS' are allowed
  "sample_num": 128,
  "log_interval": 32,
  "log_dir": "/data/logs",
  "node_rank": 0,
  "world_size": 1
}
```

**Response:**

```json
{
  "status": "started",
  "log_dir": "/data/logs/20250402_082430"
}
```

### GET /api/prove/status/{task_id}

Get the status of a running prove task.

**Response:**

```json
{
  "status": "running"
}
```

Possible status values: "running", "completed", or "failed: {error message}".

### POST /api/read_proof

Read proof logs from a directory.

**Request Body:**

```json
{
  "log_dir": "/data/logs/20250402_082430"
}
```

**Response:**

The response contains a dictionary where keys are subdirectory names and values are tuples of successful and failed proof logs.

### GET /api/health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy"
}
```

## Example Usage

### Start a proof generation task

```bash
curl -X POST "http://localhost:8000/api/prove" \
  -H "Content-Type: application/json" \
  -d '{
    "data_path": "datasets/minif2f.jsonl",
    "log_dir": "/data/logs"
  }'
```

### Check the status of a task

```bash
curl -X GET "http://localhost:8000/api/prove/status/prove_20250402_082430"
```

### Read proof logs

```bash
curl -X POST "http://localhost:8000/api/read_proof" \
  -H "Content-Type: application/json" \
  -d '{
    "log_dir": "/data/logs/20250402_082430"
  }'
