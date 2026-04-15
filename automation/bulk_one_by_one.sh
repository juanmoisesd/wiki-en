for lang in bg hr cs da nl et fi de el hu ga it lv lt mt pl pt ro sk sl sv hi zh-tw ms id ko ja ar he; do
    echo "Processing $lang"
    # Token should be provided via environment variable
    python3 automation/preprint_engine.py --source preprints_source_$lang --output preprints_pdf_$lang
done
