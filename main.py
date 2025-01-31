import re
import argparse

from vllm import LLM, SamplingParams

from prover.lean.verifier import Lean4ServerScheduler
from repository import conjecture_repository as crepo
from repository import proof_repository as prepo

def main(start_date: str = None):
    model_name = "deepseek-ai/DeepSeek-Prover-V1.5-RL"
    model = LLM(model=model_name, max_num_batched_tokens=8192, seed=1, trust_remote_code=True)

    lean4_scheduler = Lean4ServerScheduler(max_concurrent_requests=1, timeout=300, memory_limit=10, name='verifier')

    prompt = r'''Complete the following Lean 4 code:

```lean4
'''

    sampling_params = SamplingParams(
        temperature=1.0,
        max_tokens=2048,
        top_p=0.95,
        n=1,
    )

    id_conjecture_list = crepo.fetch_conjecture_datas(nontrivial_only=True, start_date=start_date)
    print(f"{len(id_conjecture_list)} conjectures fetched")
    for conjecture_id, input_seed, conjecture in id_conjecture_list:

        model_inputs = [prompt + conjecture]
        model_outputs = model.generate(
            model_inputs,
            sampling_params,
            use_tqdm=False,
        )
        result = prompt + conjecture + model_outputs[0].outputs[0].text
        print(result)
        if not result.endswith('\n```'):
            print('Proof failed!')
            continue

        request_id_list = lean4_scheduler.submit_all_request([re.search(r'```lean4\n(.*?)\n```', result, re.DOTALL).group(1)])
        outputs_list = lean4_scheduler.get_all_request_outputs(request_id_list)
        print(outputs_list[0])
        prepo.save(result[46:-3], outputs_list[0])
        if outputs_list[0]['complete']:
            print('Proof successful!')
            prepo.write_new_theorems([(conjecture_id, input_seed, result[46:-3])])


    # Expected output (verify_time may vary):
    '''{'sorries': [], 'tactics': [], 'errors': [], 'warnings': [{'severity': 'warning', 'pos': {'line': 14, 'column': 7}, 'endPos': {'line': 14, 'column': 10}, 'data': "unused variable `h₁'`\nnote: this linter can be disabled with `set_option linter.unusedVariables false`"}, {'severity': 'warning', 'pos': {'line': 15, 'column': 7}, 'endPos': {'line': 15, 'column': 10}, 'data': "unused variable `h₂'`\nnote: this linter can be disabled with `set_option linter.unusedVariables false`"}, {'severity': 'warning', 'pos': {'line': 19, 'column': 35}, 'endPos': {'line': 19, 'column': 38}, 'data': 'Used `tac1 <;> tac2` where `(tac1; tac2)` would suffice\nnote: this linter can be disabled with `set_option linter.unnecessarySeqFocus false`'}, {'severity': 'warning', 'pos': {'line': 20, 'column': 15}, 'endPos': {'line': 20, 'column': 18}, 'data': 'Used `tac1 <;> tac2` where `(tac1; tac2)` would suffice\nnote: this linter can be disabled with `set_option linter.unnecessarySeqFocus false`'}], 'infos': [], 'system_messages': '', 'system_errors': None, 'ast': {}, 'verified_code': "import Mathlib\nimport Aesop\n\nset_option maxHeartbeats 0\n\nopen BigOperators Real Nat Topology Rat\n\n/-- The second and fourth terms of a geometric sequence are $2$ and $6$. Which of the following is a possible first term?\nShow that it is $\x0crac{2\\sqrt{3}}{3}$.-/\ntheorem amc12b_2003_p6 (a r : ℝ) (u : ℕ → ℝ) (h₀ : ∀ k, u k = a * r ^ k) (h₁ : u 1 = 2)\n  (h₂ : u 3 = 6) : u 0 = 2 / Real.sqrt 3 ∨ u 0 = -(2 / Real.sqrt 3) := by\n  simp_all only [Nat.one_eq_succ_zero, Nat.zero_eq, zero_add, Nat.add_succ, Nat.add_zero,\n    Nat.succ_add]\n  have h₁' : a * r = 2 := by simpa [h₀] using h₁\n  have h₂' : a * r ^ 3 = 6 := by simpa [h₀] using h₂\n  have h₃ : r ^ 2 = 3 := by\n    nlinarith\n  have h₄ : a = 2 / Real.sqrt 3 ∨ a = -(2 / Real.sqrt 3) := by\n    apply eq_or_eq_neg_of_sq_eq_sq <;>\n    field_simp <;>\n    nlinarith\n  simpa [h₀] using h₄", 'pass': True, 'complete': True, 'verify_time': 23.28123140335083}'''

    lean4_scheduler.close()

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--start_date", type=str, default=None, help="start date of conjectures to be fetched. Format: %Y%m%d_%H%M%S")
    
    args = args.parse_args()
    start_date = args.start_date
    main(start_date)
