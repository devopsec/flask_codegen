# Flask Codegen

Generate an entire project, based on database tables, using templates

## Requirements

+ mysql
+ python ver >= 3

### Generate Everything

```
python3 -m 'pip -r requirements.txt'
sudo ln -s $(pwd)/flaskcodegen /usr/local/bin/flaskcodegen
mkdir -p <your project name>
cd <your project name>
flaskcodegen
```
