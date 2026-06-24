"""
Arquivo carregado automaticamente pelo Python antes de qualquer import.
Força implementação Python do protobuf para evitar erros em Python 3.14+
"""
import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
