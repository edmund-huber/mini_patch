Do you have textual or binary data that you need to patch?

```
>>> a = 'you say yes, i say no'
>>> b = 'you say stop, and i say go go go'
```

But you want a smaller patchfile than what difflib's `unified_diff()` creates?

```
>>> diff = '\n'.join(difflib.unified_diff(a, b))
>>> len(diff)
137
```

`mini_patch` also uses difflib's `SequenceMatcher` machinery, but it creates
tiny patches:

```
>>> patch = mini_patch.make_mini_patch(a, b)
>>> print patch
'0!d:8,2;i:11,$3$top;i:12,$4$ and;r:19,1,$1$g;i:21,$6$ go go;'
>>> len(patch)
60
```
