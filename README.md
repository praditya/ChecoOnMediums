# Checo-On-Mediums
### Formula AI Hackathon - 3D Modelling Challenge

##### Requirements:
Blender 3.0 installed
Python Conda Environment File : pyblend_environment.yml or use spec-file.txt

##### Steps to set up environment
From spec-file
```
conda create --name myenv --file spec-file.txt
```
From yml file
```
conda env create -f pyblend_environment.yml
```

Add path of environment in blender script (main)
```
sys.path.append(obsolute path + 'Anaconda3\\envs\\pyblend\\lib\\site-packages')
```
obsolute path - path of Anaconda installation (``` where python ```)

