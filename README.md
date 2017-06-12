# MT-Meld
Collocates multiple machine translation outputs for qualitative analysis

## Example Usage
```
python3 mt_meld.py --src source.txt --ref reference.txt --hyps opennmt.out nematus.out fairseq.out

Src:     Esto es una prueba
Ref:     This is a test
MT1: :-) This is a test
MT2:     That was a dog
MT3: :-) This is a test

...
```

## Other Options

### Add Google Translate Hypotheses
``` --google en ```

Argument is the target language code

### Delete BPE symbols
``` --del_bpe ```

### Truecase Outputs
``` --truecase truecase_model.txt ```

### Detokenize
``` --detok en ```

Argument is the target language code

### Lowercase All Input
``` --lc ```

### Show First *n* Lines
``` --head 5 ```
