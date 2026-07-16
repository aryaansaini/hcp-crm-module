import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = 'http://localhost:8000';


export const sendChatMessage = createAsyncThunk(
  'interaction/sendChatMessage',
  async (message) => {
    const response = await axios.post(`${API_URL}/chat`, { message });
    return response.data.response;
  }
);


export const submitInteractionForm = createAsyncThunk(
  'interaction/submitInteractionForm',
  async (formData) => {
    const response = await axios.post(`${API_URL}/interactions`, formData);
    return response.data;
  }
);

const initialState = {
  form: {
    hcpName: '',
    interactionType: 'Meeting',
    date: '',
    time: '',
    attendees: '',
    topicsDiscussed: '',
    sentiment: 'Neutral',
    outcomes: '',
    followupActions: '',
  },
  chatMessages: [],
  loading: false,
  error: null,
};

const interactionSlice = createSlice({
  name: 'interaction',
  initialState,
  reducers: {
    updateFormField: (state, action) => {
      const { field, value } = action.payload;
      state.form[field] = value;
    },
    resetForm: (state) => {
      state.form = initialState.form;
    },
    addUserMessage: (state, action) => {
      state.chatMessages.push({ role: 'user', text: action.payload });
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state) => {
        state.loading = true;
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.loading = false;
        state.chatMessages.push({ role: 'ai', text: action.payload });
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
        state.chatMessages.push({ role: 'ai', text: 'Error: could not process request.' });
      })
      .addCase(submitInteractionForm.fulfilled, (state) => {
        state.form = initialState.form;
      });
  },
});

export const { updateFormField, resetForm, addUserMessage } = interactionSlice.actions;
export default interactionSlice.reducer;
