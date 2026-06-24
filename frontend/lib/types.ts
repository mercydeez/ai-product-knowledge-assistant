export type Source = {
  rank: number;
  score: number;
  chunk_id: string;
  product_id: string;
  product_name: string;
  category: string;
  color: string;
  text: string;
};

export type AskResponse = {
  question: string;
  answer: string;
  sources: Source[];
};
