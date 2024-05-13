# Automated Preview Generator

## Description

This project provides an automated tool for generating previews of your projects in Maya, ensuring consistent camera naming conventions and storage paths. 
It simplifies the preview generation process by clearing selections, matching render settings, and managing file overwrites, making it efficient and user-friendly for CFX artists.

## Features
Camera Naming Convention: Automatically names the camera following the format Projectname_Shotnumber_Startframe_Endframe.

Storage Path Specification: Ensures previews are saved in the specified directory.
Render Settings Match: Generates preview scales matching the render settings.
Selection Clearing: Clears any selected objects before generating previews.
Filename Adherence: Generates previews following the current project filename.
File Overwrite Management: Overwrites files with the same name to maintain consistency.
Planned Additions: Switch from the selected camera to the perspective camera.

## Installation
Clone the repository:
git clone https://github.com/yourusername/automated-preview-generator.git
Navigate to the project directory:
cd automated-preview-generator
Install the required dependencies:
pip install -r requirements.txt

## Usage
Open your project in Maya.
Ensure your project filename follows the specified naming convention: Projectname_Shotnumber_Startframe_Endframe.
Run the script to generate the preview:
python generate_preview.py
Specify the storage path as required. For example:
G:\Praxis_Work_SRO\Publish\Shots\S01\cfx\ep01\SRO_ep01_004_0130\preview\CH_GumiFemale
The preview will be generated and saved in the specified directory, matching the render settings and adhering to the current project filename.

