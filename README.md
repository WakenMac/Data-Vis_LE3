# 🚀 Getting Started

Follow these steps to get the application up and running on your local machine.

### 1. Clone the Repository
First, clone the project to your local directory:
```bash
git clone [<your-repository-link-here>](https://github.com/WakenMac/Data-Vis_LE3)
cd <project-folder-name>
```

### 2. Set up the Virtual Environment
Head to the directory of the cloned repository. In there, create and activate a virtual environment to keep your dependencies isolated.

#### Create the environment
```bash
python -m venv .venv
```

#### Activate the environment
```bash
.venv\Scripts\activate
```

#### Install dependencies
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

#### For em Mac Users
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 3. Run the server
Once the environment is ready, launch the Shiny application with live reloading enabled:
```bash
shiny run --reload app.py
```

### 4. Click on the link provided in the terminal
