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
sys.path.append(absolute path + 'Anaconda3\\envs\\pyblend\\lib\\site-packages')
```
absolute path - path of Anaconda installation (``` where python ```)

##### Execution Structure:

###### A single file to fetch data and generate an output track environment
Run 'main' file (blender python script) in blender scripting mode

