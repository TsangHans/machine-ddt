from machine_ddt import DDTAgent, use_application

ddt = DDTAgent()
ddt.init()


use_application("application", "retire_exp")


ddt.run()
