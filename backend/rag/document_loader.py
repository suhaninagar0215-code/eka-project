import warnings
warnings.filterwarnings("ignore")

from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path

def load_documents():
    data_path = Path(__file__).resolve().parent.parent.parent / "data"

    if not data_path.exists():
        raise FileNotFoundError(
            f"Data directory not found: {data_path}\n"
            f"Please create a 'data' folder in your project root and add PDF files."
        )

    pdf_files = list(data_path.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in: {data_path}\n"
            f"Please add at least one PDF file to the data folder."
        )

    documents = []
    failed = []

    for file in pdf_files:
        try:
            loader = PyPDFLoader(str(file))
            docs = loader.load()

            for doc in docs:
                doc.metadata["source"] = file.name        
                doc.metadata["full_path"] = str(file)     
                doc.metadata["file_stem"] = file.stem     

            documents.extend(docs)
            print(f"Loaded: {file.name} ({len(docs)} pages)")

        except Exception as e:
            failed.append(file.name)
            print(f"Failed to load {file.name}: {str(e)}")

    if failed:
        print(f"\nWarning: {len(failed)} file(s) failed to load: {', '.join(failed)}")

    print(f"\nTotal: {len(documents)} pages loaded from {len(pdf_files) - len(failed)} files.")
    return documents


if __name__ == "__main__":
    docs = load_documents()
    print(f"\nSample metadata: {docs[0].metadata if docs else 'No docs loaded'}")