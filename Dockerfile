FROM jupyterhub/jupyterhub:0.9.4

RUN pip install git+https://github.com/sleepyprof/jupyterhub_gdietz.git
