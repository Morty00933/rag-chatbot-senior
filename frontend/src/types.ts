export type Reference = {
  document_id: number;
  filename: string;
  score: number;
  chunk_ord: number;
  preview: string;
};

export type ChatResponse = {
  answer: string;
  references: Reference[];
};
