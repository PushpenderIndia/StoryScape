# StoryScape 

## Installation
```
sudo apt install redis-server nginx python3-pip -y
sudo systemctl start redis-server
sudo systemctl enable redis-server
sudo service redis-server status 

pip install auto-gptq --no-build-isolation --extra-index-url https://huggingface.github.io/autogptq-index/whl/cu118/

pip install -r requirements.txt
```

# Run in Terminal - 1
python app.py

# Run in Terminal - 2
celery -A app.celery worker --loglevel=info
```