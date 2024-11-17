from catalyst.core.executor import Executor
# from catalyst.core.executor import Executor

# Create an executor
executor = Executor(
    hostname="localhost",
    username="yogi",
    key_filename="~/.ssh/id_rsa"
)

# Execute a command
result = executor.execute("uname -a")
print(result["stdout"])