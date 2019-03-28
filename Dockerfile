FROM jupyterhub/jupyterhub:0.9.4

LABEL maintainer="mail@gdietz.de"

RUN pip install git+https://github.com/sleepyprof/jupyterhub_gdietz.git@0.9.4_0.2

# Downgrade dockerspawner, since 0.11.0 is dysfunctional
RUN pip install dockerspawner==0.10.0

