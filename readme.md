# Meta-Terminal III

> This is the source code for the Meta-Terminal III. The Meta-Terminal III is a tool that helps the Meta Team adjust parameters with configurable interface. This tool is written in python with the modules from PyQT5.

You can run the tool from the source code by typing

```shell
python3 main.py
```

in your computer terminal under the same directory.

## Use of configuration file

The configuration file helps you define your testing interface. There are some presevered keywords and you can define your own parameters and commands so long as you follow the rules. The configuration file must be consisted with the test code and you should double check before running testing.

### Preserved keywords and commands

+ **project**: The name of the test, not important.
+ **motor_config**: A list of configurations for each motor.
+ **motor_id**: The id of the motor. The number will be fit into the command indicating the motor to which the command is sent. id should be unique and consistant with your code.
+ **motor_name**: The name for the motor, marking the motor in the interface.
+ **commands**: Put any other commands that you will need in your testing here. If the name of the parameter is not in the preserved keywords, it will be automatically recognized as a self-defined keyword. If the command may be used for each motor seperately, set the first parameter to be **"motor_id"**. If the command is only for one or more but not all motors, list the motors' names in the command and put a **"->"** before the names start. If there is neither **"motor_id"** in the first place nor **"->"**, the command will be considered a global command.