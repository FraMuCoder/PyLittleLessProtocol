# Little Less Protocol for Python

Little Less Protocol is a simple serial protocol for little microcontrollers using less memory than the most other protocols.
Of course this implementation is for the PC side communication with such a microcontroller
therefore for this implementation saving memory is not so important as for the microcontroller side.

You can find the documentation about Little Less Protocol within the
[Little Less Protocol Suite](https://github.com/FraMuCoder/LittleLessProtocolSuite).

## Getting Started

This package is currently not uploaded to Python Package Index but you can still install it via `pip`.
First you need to generate a distribution package.
On Linux go into downloaded sources and call the following commands:
```bash
python3 -m venv env
source env/bin/activate
pip install setuptools wheel
python setup.py sdist bdist_wheel
```

You will find the distribution package in `dist` folder.

To install this package in you project got into you project directory and call the following commands:
```bash
python3 -m venv env
source env/bin/activate
pip install <PATH_TO_LITTLE_LESS_PROTOCOL_FOR_PYTHON>/dist/littlelessprotocol-0.0.1-py3-none-any.whl
```

The [EchoService Example](https://github.com/FraMuCoder/LittleLessProtocolSuite/tree/main/examples/EchoService) shows how to use it.

## Links

* [Repository](https://github.com/FraMuCoder/PyLittleLessProtocol)

## License

Little Less Protocol for Python is distributed under the [MIT License](./LICENSE).
