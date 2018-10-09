from setuptools import setup

setup(name='jupyterhub_gdietz',
      version='0.1',
      description='Custom Jupyterhub Authenticator for OAuth2 with Logout and custom Spawner using docker volumes',
      author='Gunnar Dietz',
      author_email='mail@gdietz.de',
      license='BSD',
      packages=['jupyterhub_gdietz'],
      install_requires=['oauthenticator', 'dockerspawner'],
      zip_safe=False)

