import argparse
import pickle
from pathlib import Path

from domain.model.prooflog import ProofLog, Result

class ProofReader:
    def read(self, log_dir: str) -> dict[str, tuple[list[ProofLog], list[ProofLog]]]:
        """
        Read the log files and return the data.
        """
        # Read the log files
        log_path = Path(log_dir)
        if not log_path.exists():
            raise FileNotFoundError(f"Log directory {log_dir} does not exist.")
        
        # log_path直下の全てのディレクトリを取得．例えばlog_path配下にAとBというディレクトリとCというファイルがあるならAとBを取得する
        # AやBにはsuccessという名前で始まるファイルとfailureという名前で始まる.pklファイルがある
        # .pklファイルを読み込んでlist[dict]を取得する
        # [(Aのsuccess, Aのfailure), (Bのsuccess, Bのfailure), ...]のようなlistを返す
        
        result = {}
        
        # Get all subdirectories in log_path
        subdirs = [d for d in log_path.iterdir() if d.is_dir()]
        
        for subdir in subdirs:
            success_data = []
            failure_data = []
            
            # Find success and failure .pkl files
            success_files = list(subdir.glob("success*.pkl"))
            failure_files = list(subdir.glob("failure*.pkl"))
            
            # Read success files
            for success_file in success_files:
                try:
                    with open(success_file, 'rb') as f:
                        data = pickle.load(f)
                        if isinstance(data, list):
                            for item in data:
                                success_data.append(_log_from_dict(item))
                        else:
                            success_data.append(_log_from_dict(data))
                        
                except Exception as e:
                    print(f"Error reading {success_file}: {e}")
            
            # Read failure files
            for failure_file in failure_files:
                try:
                    with open(failure_file, 'rb') as f:
                        data = pickle.load(f)
                        if isinstance(data, list):
                            for item in data:
                                # print(item)
                                failure_data.append(_log_from_dict(item))
                        else:
                            failure_data.append(_log_from_dict(data))
                except Exception as e:
                    print(f"Error reading {failure_file}: {e}")
            
            # Add the tuple to the result
            result[subdir.name] = (success_data, failure_data)
        
        return result
    
def _log_from_dict(d: dict) -> ProofLog:
    """
    Convert a dictionary to a ProofLog object.
    """
    result_dict: dict = d['result']
    result = Result(
        sorries=result_dict.get('sorries',[]),
        tactics=result_dict.get('tactics', []),
        errors=result_dict.get('errors', []),
        warnings=result_dict.get('warnings', []),
        infos=result_dict.get('infos', []),
        system_messages=result_dict['system_messages'],
        system_errors=result_dict['system_errors'],
        verified_code=result_dict.get('verified_code', None),
        passed=result_dict['pass'],
        complete=result_dict['complete'],
        verify_time=result_dict['verify_time']
    )
    
    return ProofLog(
        problem_name=d['problem_name'],
        sample_info=d['sample_info'],
        formal_statement=d['formal_statement'],
        proof_code=d['proof_code'],
        result=result
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_dir", type=str, default=f'/data/logs/20250402_135940')
    log_dir = "/data/logs/20250402_135940"
    proof_reader = ProofReader()
    data = proof_reader.read(log_dir)
    for k, v in data.items():
        print(f"Directory: {k}")
        print(f"Success: {len(v[0])}, Failure: {len(v[1])}")
