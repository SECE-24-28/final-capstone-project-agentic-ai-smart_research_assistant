import React, { createContext, useContext, useState } from 'react';

const PaperContext = createContext();

export function PaperProvider({ children }) {
  const [searchResults, setSearchResults] = useState([]);
  const [selectedPapers, setSelectedPapers] = useState([]);

  const addSelectedPaper = (paper) => {
    if (!selectedPapers.find(p => p.id === paper.id)) {
      setSelectedPapers([...selectedPapers, paper]);
    }
  };

  const removeSelectedPaper = (paperId) => {
    setSelectedPapers(selectedPapers.filter(p => p.id !== paperId));
  };

  const clearSelectedPapers = () => {
    setSelectedPapers([]);
  };

  const selectedPaperIds = selectedPapers.map(p => p.id);

  return (
    <PaperContext.Provider 
      value={{ 
        searchResults, 
        setSearchResults, 
        selectedPapers, 
        addSelectedPaper, 
        removeSelectedPaper, 
        clearSelectedPapers,
        selectedPaperIds
      }}
    >
      {children}
    </PaperContext.Provider>
  );
}

export const usePaper = () => useContext(PaperContext);
