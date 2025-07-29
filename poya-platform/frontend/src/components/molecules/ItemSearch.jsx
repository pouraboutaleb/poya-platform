import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  TextField,
  Paper,
  List,
  ListItem,
  ListItemText,
  Typography,
  CircularProgress,
  Divider,
} from '@mui/material';
import {
  TreeView,
  TreeItem,
} from '@mui/x-tree-view';
import {
  ExpandMore as ExpandMoreIcon,
  ChevronRight as ChevronRightIcon,
} from '@mui/icons-material';
import { fetchCategories, searchItems, setSelectedCategory } from '../../store/itemSlice';

const renderTree = (nodes) => (
  <TreeItem key={nodes.id} nodeId={nodes.id.toString()} label={nodes.name}>
    {Array.isArray(nodes.children) && nodes.children.length > 0
      ? nodes.children.map((node) => renderTree(node))
      : null}
  </TreeItem>
);

const ItemSearch = () => {
  const dispatch = useDispatch();
  const { categories, items, loading, selectedCategory } = useSelector((state) => state.items);
  const [searchQuery, setSearchQuery] = useState('');
  
  useEffect(() => {
    dispatch(fetchCategories());
  }, [dispatch]);
  
  useEffect(() => {
    dispatch(searchItems({
      search: searchQuery,
      categoryId: selectedCategory,
    }));
  }, [dispatch, searchQuery, selectedCategory]);
  
  const handleCategorySelect = (event, nodeId) => {
    dispatch(setSelectedCategory(parseInt(nodeId)));
  };
  
  return (
    <Box sx={{ display: 'flex', gap: 2, height: '100%' }}>
      {/* Categories Tree */}
      <Paper sx={{ width: 280, p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Categories
        </Typography>
        {loading && categories.length === 0 ? (
          <Box display="flex" justifyContent="center" p={2}>
            <CircularProgress />
          </Box>
        ) : (
          <TreeView
            defaultCollapseIcon={<ExpandMoreIcon />}
            defaultExpandIcon={<ChevronRightIcon />}
            selected={selectedCategory?.toString()}
            onNodeSelect={handleCategorySelect}
            sx={{ height: '100%', overflowY: 'auto' }}
          >
            {categories.map((category) => renderTree(category))}
          </TreeView>
        )}
      </Paper>

      {/* Search and Results */}
      <Box sx={{ flex: 1 }}>
        <TextField
          fullWidth
          label="Search Items"
          variant="outlined"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          sx={{ mb: 2 }}
        />
        
        <Paper sx={{ height: 'calc(100% - 80px)', overflow: 'auto' }}>
          {loading && items.length === 0 ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : items.length > 0 ? (
            <List>
              {items.map((item) => (
                <React.Fragment key={item.id}>
                  <ListItem>
                    <ListItemText
                      primary={item.name}
                      secondary={
                        <React.Fragment>
                          <Typography component="span" variant="body2" color="text.primary">
                            {item.item_code}
                          </Typography>
                          {" - "}
                          {item.description}
                          <br />
                          <Typography component="span" variant="body2" color="text.secondary">
                            Category: {item.category_name}
                          </Typography>
                        </React.Fragment>
                      }
                    />
                  </ListItem>
                  <Divider component="li" />
                </React.Fragment>
              ))}
            </List>
          ) : (
            <Box display="flex" justifyContent="center" p={4}>
              <Typography color="text.secondary">
                No items found
              </Typography>
            </Box>
          )}
        </Paper>
      </Box>
    </Box>
  );
};

export default ItemSearch;
