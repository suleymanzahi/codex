import sys, resource, subprocess, os
import pyseccomp as seccomp




def setup_sandbox():
    try:
        if os.getuid() == 0:
            os.setgid(65534)  # nobody group
            os.setuid(65534)  # nobody user

        f = seccomp.SyscallFilter(defaction=seccomp.ALLOW)
        f.add_rule(seccomp.ERRNO(13), "unlink")
        f.add_rule(seccomp.ERRNO(13), "unlinkat")
        f.add_rule(seccomp.ERRNO(12), "mkdir")
        f.add_rule(seccomp.ERRNO(13), "rmdir")
        f.add_rule(seccomp.ERRNO(13), "rename") 

                
        f.load()

        # load the filter in the kernel
        resource.setrlimit(resource.RLIMIT_CPU, (10, 10))  # 10 sec CPU time
        resource.setrlimit(resource.RLIMIT_AS, (512*1024*1024, 512*1024*1024))  # 512MB RAM
        resource.setrlimit(resource.RLIMIT_NPROC, (20, 20))  # Max 20 processes
        resource.setrlimit(resource.RLIMIT_NOFILE, (20, 20))  # Max 20 open files
        resource.setrlimit(resource.RLIMIT_FSIZE, (10*1024*1024, 10*1024*1024))  # 10MB file size
            
    except Exception as e:
        print(f"Sandbox setup error: {e}", file=sys.stderr)
        sys.exit(1)


def run_sandbox(entry_file, timeout=5):
    try:
        result = subprocess.run(
            ["python", entry_file],
            preexec_fn=setup_sandbox,
            capture_output=True,
            timeout=timeout,
            text=True
        )
        
        return result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        return "", f"Execution timed out after {timeout} seconds"
    except Exception as e:
        return "", f"Execution error: operation not allowed"
