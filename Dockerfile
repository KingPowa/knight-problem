# Install python
FROM python:3.9
RUN mkdir -p /app/knight_simulation
RUN apt-get update \
  && apt-get install -y --no-install-recommends graphviz \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --no-cache-dir pyparsing pydot
COPY . /app/knight_simulation
WORKDIR /app/knight_simulation
RUN pip install --no-cache-dir -r requirements.txt
RUN rm /app/knight_simulation/requirements.txt

# Run the knight app when the container launches with default params
# Customize if needed
ENV row=1 \
    col=1 \
    target_col=4 \
    target_row=3 \
    board_width=8 \
    board_length=8 
CMD python knight.py $row $col $target_row $target_col -bw $board_width -bl $board_length