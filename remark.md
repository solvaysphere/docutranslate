## 翻译提示词

You will receive a sequence of original text segments to be translated, represented in JSON format. The keys are segment IDs, and the values are the text content to be translated.    
Here is the input:

<input>
```json
{json_segments}
```
</input>

For each Key-Value Pair in the JSON, translate the contents of the value into {to_lang}, Write the translation back into the value for that JSON.
> (Very important) The original text segments and translated segments must strictly correspond one-to-one. It is strictly forbidden for the IDs of the translated segments to differ from those of the original segments.
> The segment IDs in the output must exactly match those in the input. And all segment IDs in input must appear in the output.
> If necessary, two segments can only be translated together, the translation should be proportionally allocated to the corresponding key's value based on the word count ratio of the segments.

Here is an example of the expected format:

<example>
Input:

```json
{{
3:source,
4:source,
}}
```

Output(target language: {to_lang}):

```json
{{
3:translation,
4:translation,
}}
```

</example>
Please return the translated JSON directly without including any additional information and preserve special tags or untranslatable elements (such as code, brand names, technical terms) as they are.
